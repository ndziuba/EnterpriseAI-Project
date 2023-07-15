
import { MapContainer, TileLayer } from 'react-leaflet';
import { LatLngExpression } from "leaflet";
import AddMarker from './AddMarker';
import dynamic from 'next/dynamic';
import L from 'leaflet';
import React, { useEffect, useState } from 'react';

const MapIcon = dynamic(() => import('./MapIcon'), { ssr: false });

interface MapProps {
  onLatChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onLngChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const Map: React.FC<MapProps> = ({ onLatChange, onLngChange }) => {
  const [position, setPosition] = useState<LatLngExpression>([49.783333, 9.933333]);

  useEffect(() => {
    // Only import the images when the component is loaded in the browser.
    const markerIcon = require('../../public/marker-icon.png');
    const markerShadow = require('../../public/marker-shadow.png');
    //@ts-ignore
    delete L.Icon.Default.prototype._getIconUrl;

    L.Icon.Default.mergeOptions({
      iconRetinaUrl: markerIcon,
      iconUrl: markerIcon,
      shadowUrl: markerShadow
    });

  }, []);

  const handleMarkerAdd = (coord: LatLngExpression) => {
    setPosition(coord);
  };

  return (
    <div style={{ height: "400px", width: "100%" }}>
      <MapContainer center={position} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <AddMarker onMarkerAdd={handleMarkerAdd} onLatChange={onLatChange} onLngChange={onLngChange} />
        <MapIcon />
      </MapContainer>
    </div>
  );
};

export default Map;
