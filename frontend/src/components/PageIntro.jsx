export default function PageIntro({ eyebrow, title, description }) {
  return (
    <header className="mb-8">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary">
        {eyebrow}
      </p>

      <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
        {title}
      </h1>

      <p className="mt-3 max-w-2xl text-muted-foreground">{description}</p>
    </header>
  );
}
