export interface VehiclePositions {
  header: {
    gtfs_realtime_version: string;
    incrementality: string;
    timestamp: number;
  },
  entity: {
    id: string;
    vehicle: {
      trip: {
        trip_id: string;
        start_time: string;
        start_date: string;
        route_id: string;
      },
      position: {
        latitude: number;
        longitude: number;
      },
      timestamp: number;
      stop_id: string;
      current_stop_sequence: number;
    }
  }[]
}

export interface TripUpdates {
  header: {
    gtfs_realtime_version: string;
    incrementality: string;
    timestamp: number;
  },
  entity: {
    id: string;
    trip_update: {
      trip: {
        trip_id: string;
        start_time: string;
        start_date: string;
        route_id: string;
      },
      stop_time_update: {
        stop_sequence: number;
        arrival: {
          time: number;
        },
        departure: {
          time: number;
        },
        stop_id: string;
      }[]
    }
  }[]
}

export interface DataTick {
  tripUpdates: TripUpdates;
  vehiclePositions: VehiclePositions;
  timestamp: number;
}

export interface GPS {
  lat: number;
  lon: number;
};

export interface NormalVariable {
  mean: number;
  variance: number;
};
