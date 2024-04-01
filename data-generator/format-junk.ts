import { readFileSync, writeFileSync } from 'fs';

let data = JSON.parse(readFileSync("stop-infos.json", "utf-8"));
Object.keys(data.stopInfos).forEach((stopId) => {
  // remove stopTimes
  delete data.stopInfos[stopId].stopTimes;
});
writeFileSync("stop-infos.json", JSON.stringify(data, null, 2));
data = JSON.parse(readFileSync("route-infos.json", "utf-8"));
Object.keys(data.routeInfos).forEach(route => {
  Object.keys(data.routeInfos[route].routeStops).forEach(stopKey => {
    const stopTimes = data.routeInfos[route].routeStops[stopKey];
    stopTimes.forEach((stopTime: any) => {
      delete stopTime.trip;
    });
  });
});
writeFileSync("route-infos.json", JSON.stringify(data, null, 2));
