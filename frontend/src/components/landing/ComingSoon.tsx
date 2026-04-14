export function ComingSoon() {
  const upcoming = [
    {
      title: "Cost of Living",
      description: "Track inflation, consumer price index (CPI), and regional disparities in basic necessities.",
      icon: "home",
      status: "In Research",
    },
    {
      title: "Medicine & Health",
      description: "Monitor pharmaceutical supply chains, price fluctuations, and healthcare availability.",
      icon: "pill",
      status: "Data Sourcing",
    },
    {
      title: "Human Resources",
      description: "Analyze labor market trends, salary benchmarks, and employment statistics across sectors.",
      icon: "users",
      status: "Planning",
    },
  ];

  return (
    <section id="roadmap" className="relative overflow-hidden bg-neutral-100 py-24 px-6 text-neutral-900">
      {/* Subtle Grid Background */}
      <div className="absolute inset-0 z-0 opacity-40">
        <div className="absolute top-0 left-0 w-full h-full" style={{ backgroundImage: "radial-gradient(#171717 1px, transparent 1px)", backgroundSize: "24px 24px" }} />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl text-center">
        <div className="mb-6 inline-flex items-center gap-3 border-2 border-neutral-900 bg-white px-5 py-2 text-xs font-bold tracking-[0.2em] uppercase text-neutral-900 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-neutral-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-neutral-500"></span>
          </span>
          ROADMAP & FUTURE FEATURES
        </div>

        <h2 className="mb-16 text-4xl font-black uppercase tracking-tighter sm:text-6xl text-neutral-900">
          Expanding the Horizon.
        </h2>

        <div className="grid gap-6 md:grid-cols-3 text-left">
          {upcoming.map((item, idx) => (
            <div 
              key={idx} 
              className="group flex flex-col border-2 border-neutral-900 bg-white p-8 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:-translate-y-1 hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex h-12 w-12 items-center justify-center border-2 border-neutral-900 bg-neutral-50 text-neutral-900 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                  {item.icon === "home" && (
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                  )}
                  {item.icon === "pill" && (
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                  )}
                  {item.icon === "users" && (
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  )}
                </div>
                <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 border border-neutral-200 px-2 py-1 bg-neutral-50">
                  {item.status}
                </span>
              </div>
              <h3 className="mb-3 text-xl font-bold uppercase tracking-tight">{item.title}</h3>
              <p className="text-sm font-medium text-neutral-600 leading-relaxed">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}