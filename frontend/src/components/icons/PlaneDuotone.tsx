import * as React from "react";

export default function PlaneDuotone(
  props: React.SVGProps<SVGSVGElement>
) {
  return (
    <svg
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      stroke="none"
      {...props}
    >
      <path
        d="M2 12l9 3 1 7 2-6 8-1 2-3-12-9z"
        fill="currentColor"
        opacity="0.4"
      />
      <path
        d="M2 12l21-7-7 9 7 3-8 1-2 6-3-7z"
        fill="currentColor"
      />
    </svg>
  );
}
