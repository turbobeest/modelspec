import { useEffect, useId, useRef, useState } from "react";
import {
  FEEDBACK_RATINGS,
  FeedbackError,
  RATING_LABELS,
  sendFeedback,
  withdrawFeedback,
} from "./client";
import type { FeedbackRating, FeedbackResult } from "./client";

type Sent =
  | { kind: "idle" }
  | { kind: "sending" }
  | { kind: "done"; result: FeedbackResult }
  | { kind: "withdrawn" }
  | { kind: "error"; message: string };

/**
 * One piece of feedback (MODEL-221): five fixed choices, then two optional
 * text fields. Used for the per-answer prompt and for the page-wide control.
 */
export function FeedbackForm({
  question,
  decisionId = null,
  template = null,
  page,
  compact = false,
}: {
  question: string;
  decisionId?: string | null;
  template?: string | null;
  page: string;
  /** The per-answer prompt starts as a row of choices and grows on a pick. */
  compact?: boolean;
}) {
  const id = useId();
  const [rating, setRating] = useState<FeedbackRating | null>(null);
  const [note, setNote] = useState("");
  const [trying, setTrying] = useState("");
  const [sent, setSent] = useState<Sent>({ kind: "idle" });
  const status = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    if (sent.kind !== "idle" && sent.kind !== "sending") status.current?.focus();
  }, [sent.kind]);

  const submit = async () => {
    if (!rating) return;
    setSent({ kind: "sending" });
    try {
      const result = await sendFeedback({
        rating,
        client: "page",
        decision_id: decisionId ?? undefined,
        template: template ?? undefined,
        page,
        note,
        trying_to_decide: trying,
      });
      setSent({ kind: "done", result });
    } catch (error) {
      setSent({
        kind: "error",
        message: error instanceof FeedbackError ? error.message : "Feedback could not be sent.",
      });
    }
  };

  const undo = async (receipt: string) => {
    try {
      await withdrawFeedback(receipt);
      setSent({ kind: "withdrawn" });
    } catch (error) {
      setSent({
        kind: "error",
        message: error instanceof FeedbackError ? error.message : "It could not be deleted.",
      });
    }
  };

  if (sent.kind === "done" || sent.kind === "withdrawn") {
    return (
      <div className="feedback-form feedback-sent">
        <p ref={status} tabIndex={-1} role="status">
          {sent.kind === "withdrawn"
            ? "Deleted. Nothing of it is kept."
            : sent.result.status === "recorded"
              ? "Thank you. Your feedback was recorded."
              : "Thank you. Feedback storage is not switched on yet, so nothing was kept."}
          {sent.kind === "done" && sent.result.status !== "deleted" && sent.result.redacted.length > 0 &&
            ` We removed what looked like ${sent.result.redacted.map((kind) => kind.replace("_", " ")).join(", ")} before it reached us.`}
        </p>
        {sent.kind === "done" && sent.result.status === "recorded" && (
          <button type="button" className="text-button" onClick={() => {
            if (sent.result.status === "recorded") void undo(sent.result.receipt);
          }}>
            Undo and delete it
          </button>
        )}
      </div>
    );
  }

  const expanded = !compact || rating !== null;
  return (
    <form
      className="feedback-form"
      aria-label={question}
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <fieldset className="feedback-ratings">
        <legend>{question}</legend>
        {FEEDBACK_RATINGS.map((value) => (
          <label key={value} className={rating === value ? "chosen" : undefined}>
            <input
              type="radio"
              name={`${id}-rating`}
              value={value}
              checked={rating === value}
              onChange={() => setRating(value)}
            />
            {RATING_LABELS[value]}
          </label>
        ))}
      </fieldset>
      {expanded && (
        <>
          <label className="feedback-field">
            <span>
              Anything else? <em>(optional)</em>
            </span>
            <textarea
              value={note}
              maxLength={1000}
              rows={3}
              onChange={(event) => setNote(event.target.value)}
              aria-describedby={`${id}-privacy`}
            />
          </label>
          <label className="feedback-field">
            <span>
              What were you trying to decide? <em>(optional)</em>
            </span>
            <input
              type="text"
              value={trying}
              maxLength={300}
              onChange={(event) => setTrying(event.target.value)}
              aria-describedby={`${id}-privacy`}
            />
          </label>
          <p id={`${id}-privacy`} className="feedback-privacy">
            No account and no key. Please don&apos;t include prompts, keys or personal details.{" "}
            <a href="/feedback/#privacy">What we keep</a>
          </p>
          <div className="feedback-actions">
            <button type="submit" className="primary" disabled={!rating || sent.kind === "sending"}>
              {sent.kind === "sending" ? "Sending…" : "Send feedback"}
            </button>
          </div>
        </>
      )}
      {sent.kind === "error" && (
        <p ref={status} tabIndex={-1} role="alert" className="feedback-error">
          {sent.message}
        </p>
      )}
    </form>
  );
}

/** The page-wide control: a labelled button that opens the form in a dialog. */
export function FeedbackLauncher({ page }: { page: string }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [open, setOpen] = useState(false);
  const [round, setRound] = useState(0);
  const show = () => {
    setRound((n) => n + 1);
    setOpen(true);
    const node = dialog.current;
    if (node && typeof node.showModal === "function" && !node.open) node.showModal();
  };
  const close = () => {
    setOpen(false);
    if (dialog.current?.open) dialog.current.close();
  };
  return (
    <>
      <button type="button" className="feedback-launcher" onClick={show} aria-haspopup="dialog">
        Feedback
      </button>
      <dialog
        ref={dialog}
        className="feedback-dialog"
        aria-label="Feedback"
        onClose={() => setOpen(false)}
        onCancel={() => setOpen(false)}
      >
        {open && (
          <>
            <div className="feedback-dialog-head">
              <strong>Feedback</strong>
              <button type="button" className="text-button" onClick={close} aria-label="Close feedback">
                Close
              </button>
            </div>
            <FeedbackForm key={round} question="What did you think of this page?" page={page} />
          </>
        )}
      </dialog>
    </>
  );
}
