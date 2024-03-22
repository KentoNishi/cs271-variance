// 1. fetch https://passio3.com/harvard/passioTransit/gtfs/realtime/tripUpdates.json
// 2. fetch https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json
// 3. combine into { tripUpdates, vehiclePositions, timestamp } where timestamp is the time of the fetch
// 4. open "data.txt"
// 5. append one line to "data.txt" with the JSON.stringify of the combined object
// 6. repeat every 1 second

import fetch from 'node-fetch';
import fs from 'fs';

const fetchTripUpdates = async () => {
  const response = await fetch('https://passio3.com/harvard/passioTransit/gtfs/realtime/tripUpdates.json');
  return response.json();
}

const fetchVehiclePositions = async () => {
  const response = await fetch('https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json');
  return response.json();
}

setInterval(async () => {
  try {
    const tripUpdates = await fetchTripUpdates();
    const vehiclePositions = await fetchVehiclePositions();
    const timestamp = Date.now();
    const data = { tripUpdates, vehiclePositions, timestamp };
    console.log(JSON.stringify(data));
    fs.appendFileSync('./data-ignore.txt', JSON.stringify(data) + '\n');
  } catch (e) {
    console.error(e);
  }
}, 1000);
