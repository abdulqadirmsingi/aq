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
  emptyMessage?: string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = "No data available",
}: DataTableProps<T>) {
  return (
    <div className="border-[3px] border-neutral-950 bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[600px] text-left text-sm border-collapse md:min-w-full">
          <thead>
            <tr className="bg-neutral-950">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-white border-b-[3px] border-neutral-950 whitespace-nowrap"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y-[2px] divide-neutral-950">
            {data.length > 0 ? (
              data.map((item) => (
                <tr
                  key={keyExtractor(item)}
                  className="group bg-white transition-colors hover:bg-neutral-50"
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={cn(
                        "px-6 py-4 font-bold text-neutral-900 group-hover:text-black transition-colors whitespace-nowrap",
                        col.className,
                      )}
                    >
                      {col.render(item)}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr className="bg-white">
                <td
                  colSpan={columns.length}
                  className="px-6 py-8 text-center text-sm font-bold text-neutral-500 whitespace-nowrap"
                >
                  {emptyMessage}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
