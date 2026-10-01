export default function Field({label, children}) {
  return (
    <label className="block text-xs font-semibold">
      <span className="mb-1 block">{label}</span>
      {children}
    </label>
  );
}

