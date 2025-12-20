import { X } from 'lucide-react';

interface ErrorAlertProps {
  message: string;
  onClose: () => void;
}

export function ErrorAlert({ message, onClose }: ErrorAlertProps) {
  return (
    <div className="alert alert-error shadow-lg flex items-center justify-between">
      <div>
        <span>{message}</span>
      </div>
      <button onClick={onClose} className="btn btn-ghost btn-sm">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
