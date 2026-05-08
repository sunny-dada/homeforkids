/** API 클라이언트 */
import type {
  SafetyResponse,
  SearchResponse,
  NearbySchoolsResponse,
  NearbyAcademiesResponse,
} from "@/types/safety";

const BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export async function fetchSafetyScore(
  lat: number,
  lng: number,
  radius: number = 500,
  name?: string,
): Promise<SafetyResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lng: lng.toString(),
    radius: radius.toString(),
  });
  if (name) params.set("name", name);

  const res = await fetch(`${BASE}/safety/score?${params}`);
  if (!res.ok) throw new Error("API 요청 실패");
  return res.json();
}

export async function searchSuggestions(
  query: string,
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query });
  const res = await fetch(`${BASE}/search?${params}`);
  if (!res.ok) throw new Error("API 요청 실패");
  return res.json();
}

export async function fetchNearbySchools(
  lat: number,
  lng: number,
  radius: number = 500,
  name?: string,
  address?: string,
): Promise<NearbySchoolsResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lng: lng.toString(),
    radius: radius.toString(),
  });
  if (name) params.set("name", name);
  if (address) params.set("address", address);

  const res = await fetch(`${BASE}/schools/nearby?${params}`);
  if (!res.ok) throw new Error("API 요청 실패");
  return res.json();
}

export async function fetchNearbyAcademies(
  lat: number,
  lng: number,
  radius: number = 500,
  name?: string,
  address?: string,
): Promise<NearbyAcademiesResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lng: lng.toString(),
    radius: radius.toString(),
  });
  if (name) params.set("name", name);
  if (address) params.set("address", address);

  const res = await fetch(`${BASE}/academies/nearby?${params}`);
  if (!res.ok) throw new Error("API 요청 실패");
  return res.json();
}
