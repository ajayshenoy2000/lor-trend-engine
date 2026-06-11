export function Header({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <header className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p className="text-sm font-semibold text-coral">L'or Clinic YouTube</p>
        <h1 className="mt-1 text-3xl font-bold tracking-normal text-ink sm:text-4xl">{title}</h1>
      </div>
      <p className="max-w-xl text-sm leading-6 text-ink/65">{subtitle}</p>
    </header>
  );
}
