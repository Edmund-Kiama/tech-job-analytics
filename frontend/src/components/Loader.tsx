type LoaderProps = {
  label?: string;
  className?: string;
};

export default function Loader({
  label = 'Loading...',
  className = '',
}: LoaderProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex min-h-32 items-center justify-center gap-3 text-sm text-muted-foreground ${className}`}
    >
      <span
        aria-hidden="true"
        className="h-5 w-5 animate-spin rounded-full border-2 border-current border-t-transparent"
      />
      <span>{label}</span>
    </div>
  );
}
