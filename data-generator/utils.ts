// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import dist from 'gps-distance';
import { GPS, NormalVariable } from './types';
const E_SECONDS_PER_METER = 1 / 1.4;
const VAR_SECONDS_PER_METER = E_SECONDS_PER_METER / 4;

export const getDistance = (origin: GPS, destination: GPS): number => {
  return dist(origin.lat, origin.lon, destination.lat, destination.lon);
}

export const timeToWalk = (origin: GPS, destination: GPS): NormalVariable => {
  const mean = getDistance(origin, destination) * E_SECONDS_PER_METER * 1000 * 60;
  const variance = getDistance(origin, destination) * VAR_SECONDS_PER_METER * ((1000 * 60) ** 2);
  return { mean, variance };
}
