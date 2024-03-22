import { readFileSync } from 'fs';
import { DataTick, StopInfo } from './types';

const rawLines = readFileSync('./data-3-8.txt', 'utf-8').split('\n');
const lines = rawLines.map(line => {
  try {
    return JSON.parse(line);
  } catch (e) {
    return undefined;
  }
}).filter(Boolean) as DataTick[];

const stopInfos = JSON.parse(readFileSync('./stop-infos.json', 'utf-8')).stopInfos as StopInfo[];
