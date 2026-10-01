export default function ChartPlaceholder({title}) {
  return (
    <section className="card grid min-h-56 place-items-center p-6 text-center text-slate-500">
      <div><h3 className="font-bold text-slate-800">{title}</h3><p>Chart data will appear after transactions are recorded.</p></div>
    </section>
  );
}

