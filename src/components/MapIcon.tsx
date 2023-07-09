import { useEffect } from 'react';
import L from 'leaflet';

const MapIcon = () => {
  useEffect(() => {
    // @ts-expect-error type definition is missing for leaflet default icon
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
      iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
      shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    });
  }, []);

  return null;
};

export default MapIcon;
