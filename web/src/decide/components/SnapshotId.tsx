const description = "The data version this answer used";

export function SnapshotId({ snapshot }: { snapshot: string }) {
  const resolved = snapshot !== "latest";
  return <span className="snapshot" title={resolved ? description : undefined} aria-description={resolved ? description : undefined} tabIndex={resolved ? 0 : undefined}>
    {snapshot}
  </span>;
}
