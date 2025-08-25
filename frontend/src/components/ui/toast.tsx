import * as React from "react";

interface Toast {
  id: number;
  title: string;
}

const ToastContext = React.createContext<(msg: string) => void>(() => {});
export const useToast = () => React.useContext(ToastContext);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const add = React.useCallback((title: string) => {
    const id = Date.now();
    setToasts((t) => [...t, { id, title }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3000);
  }, []);

  return (
    <ToastContext.Provider value={add}>
      {children}
      <div className="fixed top-4 right-4 space-y-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className="bg-gray-800 text-neon-green border border-neon-blue px-4 py-2 rounded shadow"
          >
            {t.title}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
