export interface ApiPageMeta {
  limit: number;
  offset: number;
  total: number;
  has_next: boolean;
}

export interface ApiPage<T> {
  items: T[];
  meta: ApiPageMeta;
}
