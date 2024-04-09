import { readFileSync } from 'fs';
import { DataTick, GPS, NormalVariable, StopInfo } from './types';
import { timeToWalk } from './utils';
import { writeFileSync } from 'fs';

const rawLines = readFileSync('./data-3-8.txt', 'utf-8').split('\n');
const lines = rawLines.map((line: string) => {
  try {
    return JSON.parse(line);
  } catch (e) {
    return undefined;
  }
}).filter(Boolean) as DataTick[];

const stopInfos = JSON.parse(readFileSync('./stop-infos.json', 'utf-8')).stopInfos as Record<string, StopInfo>;

// for each trip, keep track of the "current" stop_id and the time at which the stop_id was set to that value
// for each line in the data, if the current stop_id changes, calculate the difference in time between the current time and the time at which the previous stop_id was set
// in a dict which keeps track of every pair of stop_ids, add that difference to the list of differences
// at the end, calculate the mean and variance of the differences

interface Tracker {
  currentStopId: string;
  lastUpdateTime: number;
}

const vehicleTrackers: Record<string, Tracker> = {};
const stopIdPairs: Record<string, number[]> = {};

for (const line of lines) {
  for (const entity of line.vehiclePositions.entity) {
    const { id, vehicle: { timestamp, stop_id }} = entity;
    const newTracker = {
      currentStopId: stop_id,
      lastUpdateTime: timestamp,
    };
    if (!vehicleTrackers[id]) {
      vehicleTrackers[id] = newTracker;
    }
    const oldTracker = vehicleTrackers[id];
    if (stop_id !== oldTracker.currentStopId) {
      const [x, y] = [
        Math.min(parseInt(stop_id),
        parseInt(oldTracker.currentStopId)), Math.max(parseInt(stop_id), parseInt(oldTracker.currentStopId))
      ];
      const key = `${x} => ${y}`;
      const diff = timestamp - oldTracker.lastUpdateTime;
      if (Math.abs(diff) > 1000 && Math.abs(diff) < 60 * 1000 * 20) {
        if (!stopIdPairs[key]) {
          stopIdPairs[key] = [];
        }
        stopIdPairs[key].push(diff);
        vehicleTrackers[id] = newTracker;
      }
    }
  }
}

// only keep stop_id pairs with more than 3 data points
const filteredStopIdPairs = Object.entries(stopIdPairs).filter(([_, values]) => values.length > 3);

// construct a directed graph where each node is a stop_id and each edge is a pair of stop_ids
// the weight of each edge is the mean of the differences between the stop_ids in the pair
// for each edge, also calculate the variance of the differences and store it in the edge
// construct findShortestPathBetweenStops function which uses Dijkstra's algorithm to find the shortest path between two nodes
// construct findShortestPathBetweenGps function which uses the above function to find the shortest path between two GPS coordinates
  // for the start and end GPS coordinates, just insert a new node into the graph with the GPS coordinates as the stop_id
  // we can use timeToWalk to calculate the mean and variance of the time it takes to walk to/from the coordinates to all the other stops
  // to get the gps coordinates of each stop while augmenting the graph, use stopInfos

interface Edge {
  from: string;
  to: string;
  meanTime: number;
  varianceTime: number;
}

interface Graph {
  [key: string]: Edge[];
}

const calculateMeanAndVariance = (times: number[]): NormalVariable => {
  const mean = times.reduce((a, b) => a + b, 0) / times.length;
  const variance = times.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / times.length;
  return { mean, variance };
};

const addWalkingEdgesToGraph = (origin: GPS, destination: GPS) => {
  Object.values(stopInfos).forEach(stop => {
    const stopGPS: GPS = { lat: stop.stop_lat, lon: stop.stop_lon };
    const toStop = timeToWalk(origin, stopGPS);
    const fromStop = timeToWalk(stopGPS, destination);

    if (!graph[origin.lat + ',' + origin.lon]) {
      graph[origin.lat + ',' + origin.lon] = [];
    }
    graph[origin.lat + ',' + origin.lon].push({
      from: origin.lat + ',' + origin.lon,
      to: stop.stop_id,
      meanTime: toStop.mean,
      varianceTime: toStop.variance,
    });

    if (!graph[stop.stop_id]) {
      graph[stop.stop_id] = [];
    }
    graph[stop.stop_id].push({
      from: stop.stop_id,
      to: destination.lat + ',' + destination.lon,
      meanTime: fromStop.mean,
      varianceTime: fromStop.variance,
    });
    if (!graph[destination.lat + ',' + destination.lon]) {
      graph[destination.lat + ',' + destination.lon] = [];
    }
  });

  // add direct walking edge between origin and destination
  const toDestination = timeToWalk(origin, destination);
  graph[origin.lat + ',' + origin.lon].push({
    from: origin.lat + ',' + origin.lon,
    to: destination.lat + ',' + destination.lon,
    meanTime: toDestination.mean,
    varianceTime: toDestination.variance,
  });
};

const constructGraph = (filteredStopIdPairs: [string, number[]][]): Graph => {
  const graph: Graph = {};
  filteredStopIdPairs.forEach(([key, values]) => {
    const [from, to] = key.split(' => ');
    const { mean, variance } = calculateMeanAndVariance(values);
    if (!graph[from]) {
      graph[from] = [];
    }
    graph[from].push({ from, to, meanTime: mean, varianceTime: variance });
  });
  return graph;
};

function dijkstra(start: string, end: string): { distance: number, path: string[] } {
  const distances: { [node: string]: number } = {};
  const previous: { [node: string]: string | null } = {};
  const seen: Set<string> = new Set();
  const queue: string[] = [start];

  // Initialize all distances to Infinity and previous nodes to null
  for (let node in graph) {
    distances[node] = node === start ? 0 : Infinity;
    previous[node] = null;
  }

  while (queue.length > 0) {
    // Find the node with the minimum distance from the queue
    let current = queue.reduce((minNode, node) => (distances[node] < distances[minNode] ? node : minNode), queue[0]);

    // If we reached the end node, break out of the loop
    if (current === end) {
      break;
    }

    seen.add(current);
    const currentDistance = distances[current];
    const edges = graph[current];

    for (let edge of edges) {
      const distance = currentDistance + edge.meanTime;
      if (distance < distances[edge.to]) {
        distances[edge.to] = distance;
        previous[edge.to] = current;
        if (!seen.has(edge.to)) {
          queue.push(edge.to);
        }
      }
    }

    // Remove the current node from the queue
    queue.splice(queue.indexOf(current), 1);
  }

  // Reconstruct the path
  const path = [];
  let currentNode = end;
  while (currentNode !== null && currentNode in previous) {
    path.unshift(currentNode);
    currentNode = previous[currentNode] as string;
  }

  // console.log(distances, path);

  // Check if a path exists
  if (path[0] !== start) {
    return { distance: -1, path: [] }; // Indicates no path exists
  }

  return {
    distance: distances[end],
    path: path,
  };
}


let graph = constructGraph(filteredStopIdPairs);

const findShortestPathBetweenGps = (origin: GPS, destination: GPS) => {
  addWalkingEdgesToGraph(origin, destination);
  return dijkstra(`${origin.lat},${origin.lon}`, `${destination.lat},${destination.lon}`);
}

// top left: 42.383850169141745, -71.13409264574024
// top right: 42.383850169141745, -71.10504224250766
// bottom left: 42.36020227811244, -71.13409264574024
// bottom right: 42.36020227811244, -71.10504224250766
// the grid will be formed by a 100x100 matrix of points, with corners aligned (meaning the region is split into 99x99=9801 rectangles, with each corner of the rectangles corresponding to a point)
// the increments of the grid points will be uniform
// the origin is 42.36340914857679, -71.12589555981565

const meanTimeGrid: number[][] = Array(100).fill(0).map(() => Array(100).fill(0));
const varianceTimeGrid: number[][] = Array(100).fill(0).map(() => Array(100).fill(0));
const masterOrigin = { lat: 42.36340914857679, lon: -71.12589555981565 };
for (let i = 0; i < 100; i++) {
  console.log(i);
  for (let j = 0; j < 100; j++) {
    const originalGraph = JSON.parse(JSON.stringify(graph));
    const destination: GPS = {
      lat: 42.383850169141745 + (42.36020227811244 - 42.383850169141745) * (i) / (100 - 1),
      lon: -71.13409264574024 + (-71.10504224250766 + 71.13409264574024) * (j) / (100 - 1),
    };
    const { distance, path } = findShortestPathBetweenGps(masterOrigin, destination);
    meanTimeGrid[i][j] = distance / (1000);
    let variance = 0;
    // console.log(i, j, meanTimeGrid[i][j], path);
    for (let k = 0; k < path.length - 1; k++) {
      const edge = graph[path[k]].find(edge => edge.to == path[k + 1]);
      variance += edge!.varianceTime;
    }
    varianceTimeGrid[i][j] = variance / (1000 ** 2);
    graph = JSON.parse(JSON.stringify(originalGraph));
  }
}
// console.log(meanTimeGrid, varianceTimeGrid);

writeFileSync('./meanTimeGrid.json', JSON.stringify(meanTimeGrid));
writeFileSync('./varianceTimeGrid.json', JSON.stringify(varianceTimeGrid));
writeFileSync('./graph.json', JSON.stringify(graph));
writeFileSync('./timeGridInfo.json', JSON.stringify({
  origin: masterOrigin,
  topLeft: { lat: 42.383850169141745, lon: -71.13409264574024 },
  topRight: { lat: 42.383850169141745, lon: -71.10504224250766 },
  bottomLeft: { lat: 42.36020227811244, lon: -71.13409264574024 },
  bottomRight: { lat: 42.36020227811244, lon: -71.10504224250766 },
}));
