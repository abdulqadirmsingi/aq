export function DataFeatures() {
  const features = [
    {
      title: "Energy & Fuel Prices",
      description: "Track historical and real-time fuel prices across regions from EWURA. Analyze trends, regional price differences, and historical extremes to optimize logistics and planning.",
      icon: (
        <svg className="h-8 w-8 text-neutral-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      accent: "bg-amber-100",
    },
    {
      title: "Exchange Rates",
      description: "Monitor Bank of Tanzania (BOT) exchange rates. Track spreads, benchmark gaps, and identify opportunities with our advanced analytics and historical comparison tools.",
      icon: (
        <svg className="h-8 w-8 text-neutral-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      accent: "bg-emerald-100",
    },
    {
      title: "Stock Market (DSE)",
      description: "Get insights into the Dar es Salaam Stock Exchange. Track market capitalization, volume, and individual stock performance with our comprehensive dashboard.",
      icon: (
        <svg className="h-8 w-8 text-neutral-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      accent: "bg-blue-100",
    },
    {
      title: "Energy Monitoring",
      description: "Real-time tracking of energy consumption and grid status. Identify anomalies and optimize usage patterns with advanced telemetry data.",
      icon: (
        <svg className="h-8 w-8 text-neutral-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      accent: "bg-rose-100",
    },
  ];

  return (
    <section id="data" className="relative bg-neutral-50 py-24 px-6 text-neutral-900 border-y-2 border-neutral-900">
      <div className="mx-auto max-w-7xl">
        <div className="mb-16 flex flex-col items-start justify-between gap-6 md:flex-row md:items-end">
          <div className="max-w-2xl border-2 border-neutral-900 bg-white p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h2 className="mb-4 text-3xl font-black uppercase tracking-tight sm:text-5xl">
              Available Intelligence.
            </h2>
            <p className="text-lg font-medium text-neutral-600">
              We aggregate, clean, and analyze data from multiple sectors to provide you with decision-ready intelligence.
            </p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:gap-8">
          {features.map((feature, idx) => (
            <div 
              key={idx} 
              className="group relative flex flex-col justify-between border-2 border-neutral-900 bg-white p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
            >
              <div className={`mb-6 inline-flex border-2 border-neutral-900 ${feature.accent} p-3 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]`}>
                {feature.icon}
              </div>
              <h3 className="mb-3 text-2xl font-bold uppercase tracking-tight">{feature.title}</h3>
              <p className="text-base font-medium leading-relaxed text-neutral-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}