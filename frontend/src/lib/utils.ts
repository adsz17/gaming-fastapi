export function cn(...classes: (string | undefined | false | null)[]) {
  return classes.filter(Boolean).join(" ");
}

export function formatMoney(n: number) {
  return `$${n.toFixed(2)}`;
}

export function formatMultiplier(x: number) {
  return `${x.toFixed(2)}x`;
}
