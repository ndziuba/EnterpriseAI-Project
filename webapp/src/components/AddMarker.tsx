import { useEffect, useState } from "react";
import { Marker, useMapEvents } from "react-leaflet";
import { LatLngExpression } from 'leaflet';

interface AddMarkerProps {
  onMarkerAdd: (coord: LatLngExpression) => void;
  onLatChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onLngChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const AddMarker: React.FC<AddMarkerProps> = ({ onMarkerAdd, onLatChange, onLngChange }) => {
  const [coord, setCoord] = useState<LatLngExpression | null>(null);

  const handleMapClick = (e: any) => {
    setCoord(e.latlng);
    onMarkerAdd(e.latlng);
    onLatChange({ target: { value: e.latlng.lat } } as React.ChangeEvent<HTMLInputElement>);
    onLngChange({ target: { value: e.latlng.lng } } as React.ChangeEvent<HTMLInputElement>);
  }

  useMapEvents({
    click: handleMapClick,
  });

  return (
    coord && (
      <Marker
        key={`marker-1`}
        position={coord}
        draggable={true}
        eventHandlers={{
          dragend: (e) => {
            const position = e.target.getLatLng();
            setCoord(position);
            onMarkerAdd(position);
            onLatChange({ target: { value: position.lat } } as React.ChangeEvent<HTMLInputElement>);
            onLngChange({ target: { value: position.lng } } as React.ChangeEvent<HTMLInputElement>);
          }
        }}
      />
    )
  );
};

export default AddMarker;
