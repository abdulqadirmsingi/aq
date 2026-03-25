import { SIMULATED_DELAY_MS } from "@/lib/constants";
import { delay } from "@/lib/utils";

export async function simulateFetch<T>(data: T): Promise<T> {
  await delay(SIMULATED_DELAY_MS);
  return structuredClone(data);
}
