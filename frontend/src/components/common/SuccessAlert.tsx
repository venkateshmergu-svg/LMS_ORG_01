import { Check } from 'lucide-react';

interface SuccessAlertProps {
  message: string;
  onClose: () => void;
}

export function SuccessAlert({ message, onClose }: SuccessAlertProps) {
  return (
    <div className="alert alert-success shadow-lg flex items-center justify-between">
      <div>
        <Check className="w-5 h-5" />
        <span>{message}</span>
      </div>
      <button onClick={onClose} className="btn btn-ghost btn-sm">
        ✕
      </button>
    </div>
  );
}
