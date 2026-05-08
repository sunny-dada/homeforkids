/** 카카오맵 컴포넌트 - 선택된 아파트 위치 표시 */
import { useEffect, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { MapPin } from "lucide-react";

interface MapViewProps {
  lat: number;
  lng: number;
  name: string;
  address: string;
}

declare global {
  interface Window {
    kakao: any;
  }
}

export function MapView({ lat, lng, name, address }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);

  useEffect(() => {
    const KAKAO_JS_KEY = import.meta.env.VITE_KAKAO_JS_KEY;
    console.log("KAKAO_JS_KEY:", KAKAO_JS_KEY);
    console.log("API Key exists:", !!KAKAO_JS_KEY);

    if (!KAKAO_JS_KEY || KAKAO_JS_KEY === "여기에_발급받은_JavaScript_키를_입력하세요") {
      console.log("API Key missing or default value");
      return;
    }

    // 카카오맵 SDK 동적 로드
    const loadKakaoMap = () => {
      if (window.kakao && window.kakao.maps) {
        initializeMap();
        return;
      }

      const script = document.createElement("script");
      script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_JS_KEY}&autoload=false&t=${Date.now()}`;
      script.async = true;
      script.onload = () => {
        window.kakao.maps.load(() => {
          initializeMap();
        });
      };
      document.head.appendChild(script);
    };

    const initializeMap = () => {
      if (!mapContainer.current || mapInstance.current) return;

      const options = {
        center: new window.kakao.maps.LatLng(lat, lng),
        level: 3,
      };

      const map = new window.kakao.maps.Map(mapContainer.current, options);
      mapInstance.current = map;

      // 마커 추가
      const markerPosition = new window.kakao.maps.LatLng(lat, lng);
      const marker = new window.kakao.maps.Marker({
        position: markerPosition,
      });
      marker.setMap(map);

      // 인포윈도우 추가
      const infowindow = new window.kakao.maps.InfoWindow({
        content: `<div style="padding:8px 12px;font-size:12px;font-weight:600;white-space:nowrap;">${name}</div>`,
      });
      infowindow.open(map, marker);
    };

    loadKakaoMap();

    return () => {
      if (mapInstance.current) {
        mapInstance.current = null;
      }
    };
  }, [lat, lng, name]);

  const KAKAO_JS_KEY = import.meta.env.VITE_KAKAO_JS_KEY;

  if (!KAKAO_JS_KEY || KAKAO_JS_KEY === "여기에_발급받은_JavaScript_키를_입력하세요") {
    return (
      <Card>
        <CardContent className="py-6 flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-background-second flex items-center justify-center">
            <MapPin className="w-6 h-6 text-foreground-muted" />
          </div>
          <div className="flex flex-col items-center gap-1">
            <span className="text-sm font-semibold text-foreground">
              지도를 표시하려면 API 키가 필요합니다
            </span>
            <span className="text-xs text-foreground-muted text-center">
              .env.local 파일에 VITE_KAKAO_JS_KEY를 설정하세요
            </span>
            <a
              href="https://developers.kakao.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-primary hover:underline mt-1"
            >
              카카오 개발자 센터에서 발급 ↗
            </a>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-0">
        <div
          ref={mapContainer}
          className="w-full h-[240px] md:h-[calc(100vh-200px)] rounded-lg overflow-hidden"
        />
        <div className="px-4 py-3 border-0 border-t border-solid border-border">
          <div className="flex items-start gap-2">
            <MapPin className="w-4 h-4 text-primary flex-none mt-0.5" />
            <div className="flex flex-col gap-0.5">
              <span className="text-sm font-semibold text-foreground">
                {name}
              </span>
              <span className="text-xs text-foreground-second">{address}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
