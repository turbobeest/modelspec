import { useId } from "react";

const description = "The data version this answer used";

export function SnapshotId({ snapshot }: { snapshot: string }) {
  const id = useId();
  if (snapshot === "latest") return <span className="snapshot">{snapshot}</span>;
  // A visible tooltip on hover and keyboard focus, same pattern as RankedAnswer's route tips.
  return <span className="snapshot-wrap">
    <span className="snapshot" tabIndex={0} aria-describedby={id}>{snapshot}</span>
    <span className="snapshot-tip" role="tooltip" id={id}>{description}</span>
  </span>;
}
