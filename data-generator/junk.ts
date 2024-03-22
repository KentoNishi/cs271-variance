import { readFileSync, writeFileSync } from "fs";

const data = JSON.parse(readFileSync("jsonified.json", "utf-8"));
Object.keys(data.stopInfos).forEach((stopId) => {
  // remove stopTimes
  delete data.stopInfos[stopId].stopTimes;
});
writeFileSync("jsonified.json", JSON.stringify(data, null, 2));
