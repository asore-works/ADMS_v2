import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Home from "./page";

describe("Home", () => {
  it("renders ADMS - Phase 0", () => {
    render(<Home />);
    expect(screen.getByText("ADMS - Phase 0")).toBeDefined();
  });
});
