import { Component } from "react";
import type { ReactNode } from "react";

/**
 * Keeps one failing part of the answer from blanking the page (MODEL-294).
 * The facets sit outside it and stay usable; a new answer (`resetKey`) or
 * Reset clears the failure.
 */
export class AnswerBoundary extends Component<
  { children: ReactNode; onReset: () => void; resetKey: unknown },
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidUpdate(previous: { resetKey: unknown }) {
    if (this.state.failed && previous.resetKey !== this.props.resetKey)
      this.setState({ failed: false });
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <div role="alert" className="error" aria-label="The answer could not be shown">
        <div>
          <strong>The answer could not be shown.</strong>
          <p>
            Part of it failed to draw. Your facets still work: change one, or
            reset to the default board.
          </p>
        </div>
        <button
          className="ink-button"
          onClick={() => {
            this.setState({ failed: false });
            this.props.onReset();
          }}
        >
          Reset
        </button>
      </div>
    );
  }
}
