export default function Panel({ children, className = '' }) {
  return <section className={`glass rounded-2xl ${className}`}>{children}</section>;
}
