import React, { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import { AgentLayout } from '../../components/AgentLayout';
import { 
  Navigation, MapPin, Clock, Zap, Compass, Download 
} from 'lucide-react';

export function GPSTrackingPage() {
  const [currentLocation, setCurrentLocation] = useState(null);
  const [locationHistory, setLocationHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tracking, setTracking] = useState(false);
  const [stats, setStats] = useState({
    totalDistance: 0,
    averageSpeed: 0,
    maxSpeed: 0,
    timeElapsed: 0
  });
  
  const watchIdRef = useRef(null);

  // Start GPS tracking
  const startTracking = () => {
    if (!navigator.geolocation) {
      toast.error('Geolocation not supported in your browser');
      return;
    }

    setTracking(true);
    toast.success('GPS Tracking started - allow location access in browser');
    
    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        const speed = position.coords.speed || 0;
        
        const locationData = {
          latitude,
          longitude,
          accuracy,
          speed: Math.round(speed * 3.6), // Convert m/s to km/h
          timestamp: new Date()
        };
        
        updateLocation(locationData);
        
        setCurrentLocation(locationData);
        
        setLocationHistory(prev => [...prev, {
          latitude,
          longitude,
          speed: Math.round(speed * 3.6),
          timestamp: new Date()
        }]);
      },
      (error) => {
        console.error('Geolocation error:', error);
        toast.error('Error getting location: ' + error.message);
        setTracking(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  // Stop GPS tracking
  const stopTracking = () => {
    if (watchIdRef.current) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      setTracking(false);
      toast.success('Tracking stopped');
    }
  };

  // Update location on backend
  const updateLocation = async (locationData) => {
    try {
      const { locationAPI } = await import('../../services/api');
      await locationAPI.updateLocation({
        latitude: locationData.latitude,
        longitude: locationData.longitude,
        accuracy: locationData.accuracy,
        speed: locationData.speed
      });
    } catch (error) {
      console.error('Error updating location on backend:', error);
    }
  };

  // Load current location
  const loadCurrentLocation = async () => {
    setLoading(true);
    try {
      const { locationAPI } = await import('../../services/api');
      const response = await locationAPI.getCurrentLocation();
      setCurrentLocation(response.data);
    } catch (error) {
      console.log('Current location not available yet');
    } finally {
      setLoading(false);
    }
  };

  // Load location history
  const loadHistory = async (hours = 24) => {
    setLoading(true);
    try {
      const { locationAPI } = await import('../../services/api');
      const response = await locationAPI.getLocationHistory(hours);
      
      const data = response.data;
      setLocationHistory(data.locations);
      setStats({
        totalDistance: data.total_distance,
        averageSpeed: Math.round(data.average_speed),
        maxSpeed: Math.max(...data.locations.map(l => l.speed || 0)),
        timeElapsed: data.locations.length
      });
    } catch (error) {
      console.log('Location history not available yet');
    } finally {
      setLoading(false);
    }
  };

  // Export tracking data
  const exportTrackingData = () => {
    const data = {
      currentLocation,
      history: locationHistory,
      stats,
      exportedAt: new Date()
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `gps-tracking-${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    toast.success('Tracking data exported');
  };

  useEffect(() => {
    loadCurrentLocation();
    loadHistory(24);
  }, []);

  return (
    <AgentLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">📍 GPS Tracking</h1>
        <p className="text-gray-600">Real-time location tracking and delivery route visualization</p>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex flex-wrap gap-4">
            {!tracking ? (
              <button
                onClick={startTracking}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center gap-2 transition"
              >
                <Navigation className="w-5 h-5" /> Start Tracking
              </button>
            ) : (
              <button
                onClick={stopTracking}
                className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium flex items-center gap-2 transition"
              >
                <Navigation className="w-5 h-5" /> Stop Tracking
              </button>
            )}
            
            <button
              onClick={() => loadHistory(24)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition"
            >
              Refresh
            </button>
            
            <button
              onClick={exportTrackingData}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium flex items-center gap-2 transition"
            >
              <Download className="w-5 h-5" /> Export
            </button>
          </div>
          
          {tracking && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-medium">✓ GPS Tracking Active - Updating location every 5-10 seconds</p>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Distance</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {stats.totalDistance.toFixed(2)} km
                </p>
              </div>
              <MapPin className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-green-50 rounded-lg p-6 border border-green-200">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-green-600 text-sm font-medium">Avg Speed</p>
                <p className="text-3xl font-bold text-green-900 mt-2">
                  {stats.averageSpeed} km/h
                </p>
              </div>
              <Zap className="w-8 h-8 text-green-400" />
            </div>
          </div>

          <div className="bg-orange-50 rounded-lg p-6 border border-orange-200">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-orange-600 text-sm font-medium">Max Speed</p>
                <p className="text-3xl font-bold text-orange-900 mt-2">
                  {stats.maxSpeed} km/h
                </p>
              </div>
              <Compass className="w-8 h-8 text-orange-400" />
            </div>
          </div>

          <div className="bg-purple-50 rounded-lg p-6 border border-purple-200">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-purple-600 text-sm font-medium">Location Updates</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {locationHistory.length}
                </p>
              </div>
              <Clock className="w-8 h-8 text-purple-400" />
            </div>
          </div>
        </div>

        {/* Current Location Info */}
        {currentLocation && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Location</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Latitude</p>
                <p className="text-xl font-mono font-bold mt-1">{currentLocation.latitude.toFixed(4)}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Longitude</p>
                <p className="text-xl font-mono font-bold mt-1">{currentLocation.longitude.toFixed(4)}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Accuracy</p>
                <p className="text-xl font-mono font-bold mt-1">±{currentLocation.accuracy?.toFixed(1)}m</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Speed</p>
                <p className="text-xl font-mono font-bold mt-1">{currentLocation.speed || 0} km/h</p>
              </div>
            </div>
            
            <p className="text-sm text-gray-500 mt-4">
              Last Updated: {new Date(currentLocation.last_updated || currentLocation.timestamp).toLocaleString()}
            </p>
          </div>
        )}

        {/* Location History Table */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Location History (Last 20)</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">#</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Time</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Latitude</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Longitude</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Speed</th>
                </tr>
              </thead>
              <tbody>
                {locationHistory.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="py-8 px-4 text-center text-gray-500">
                      No location history yet. Start tracking to capture your movements.
                    </td>
                  </tr>
                ) : (
                  locationHistory.slice(-20).reverse().map((location, idx) => (
                    <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">{locationHistory.length - idx}</td>
                      <td className="py-3 px-4">
                        {new Date(location.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-gray-600">
                        {location.latitude.toFixed(4)}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-gray-600">
                        {location.longitude.toFixed(4)}
                      </td>
                      <td className="py-3 px-4 text-right font-semibold">
                        {location.speed || '-'} km/h
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h4 className="font-semibold text-blue-900 mb-2">📱 How to Use GPS Tracking</h4>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>✓ Click "Start Tracking" to begin recording your location</li>
            <li>✓ Allow location access when browser prompts</li>
            <li>✓ Location updates every 5-10 seconds automatically</li>
            <li>✓ View real-time stats (distance, speed, accuracy)</li>
            <li>✓ Click "Export" to download tracking data as JSON</li>
            <li>✓ History persists for the last 24 hours</li>
          </ul>
        </div>
      </div>
    </AgentLayout>
  );
}