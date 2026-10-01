export default function EmptyState({children = 'No records found.'}) {
  return <p className="p-8 text-center text-slate-500">{children}</p>;
}

