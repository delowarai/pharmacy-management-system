export default function StatCard({label, value, className = ''}) {
  return (
    <article className={`rounded-2xl p-5 text-white ${className}`}>
      <p className="text-sm opacity-80">{label}</p>
      <p className="mt-2 text-2xl font-black">{value}</p>
    </article>
  );
}

