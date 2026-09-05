export default function PageIntro({ eyebrow, title, description }) {
  return (
    <header className="page-intro mb-8">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
        {eyebrow}
      </p>

      <h1 className="mt-2 max-w-3xl text-4xl font-semibold leading-[0.98] sm:text-6xl">
        {title}
      </h1>

      <p className="mt-5 max-w-2xl border-l-2 border-primary pl-4 text-muted-foreground">
        {description}
      </p>
    </header>
  );
}
