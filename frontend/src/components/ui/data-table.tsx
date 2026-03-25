import { cn } from "@/lib/utils";

interface Column<T> {
  key: string;
  header: string;
  render: (item: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
}

export function DataTable<T>({ columns, data, keyExtractor }: DataTableProps<T>) {
  return (
    <div className="overflow-hidden border-[3px] border-neutral-950 bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
      <table className="w-full text-left text-sm border-collapse">
        <thead>
          <tr className="bg-neutral-950">
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-white border-b-[3px] border-neutral-950"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y-[2px] divide-neutral-950">
          {data.map((item) => (
            <tr key={keyExtractor(item)} className="bg-white transition-colors hover:bg-neutral-50 group">
              {columns.map((col) => (
                <td key={col.key} className={cn(
                  "px-6 py-4 font-bold text-neutral-900 group-hover:text-black transition-colors",
                  col.className
                )}>
                  {col.render(item)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
