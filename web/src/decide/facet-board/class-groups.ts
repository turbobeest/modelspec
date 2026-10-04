import type { Row } from "../adapter";
import { CLASS_OF_TYPE } from "../vocabulary";
import type { Vocabulary } from "../vocabulary";

/** Class labels and model names give an unranked board a neutral order. */
export function groupRowsByClass(rows: readonly Row[], vocabulary: Vocabulary | null) {
  const classes = vocabulary?.facets.find((facet) => facet.id === "model.class")?.values;
  const groups = new Map<string, { id: string; label: string; rows: Row[] }>();
  for (const row of rows) {
    const id = vocabulary?.models[`${row.m.lab}/${row.m.id}`]?.class
      ?? (row.m.type === null ? null : CLASS_OF_TYPE[row.m.type]);
    const key = id ?? "unrecorded";
    const label = classes?.find((item) => item.value === id)?.label
      ?? (id ? id.replaceAll("-", " ") : "Class not recorded");
    const group = groups.get(key);
    if (group) group.rows.push(row);
    else groups.set(key, { id: key, label, rows: [row] });
  }
  return [...groups.values()]
    .sort((left, right) => left.label.localeCompare(right.label, "en") || left.id.localeCompare(right.id, "en"))
    .map((group) => ({
      ...group,
      rows: group.rows.sort((left, right) => left.m.name.localeCompare(right.m.name, "en")),
    }));
}
