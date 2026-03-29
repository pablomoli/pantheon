'use client';

import { type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

interface SlidePanelProps {
  open: boolean;
  onClose: () => void;
  title: string;
  width?: string;   // Tailwind width class, default 'w-96'
  children: ReactNode;
}

export default function SlidePanel({
  open,
  onClose,
  title,
  width = 'w-96',
  children,
}: SlidePanelProps) {
  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 bg-linen/50 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            key="panel"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 340, damping: 32 }}
            className={`fixed right-0 top-0 h-full ${width} z-50 glass-panel border-l border-gold/20 shadow-gold flex flex-col`}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gold/10 shrink-0">
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-gold-dark">
                {title}
              </span>
              <button
                onClick={onClose}
                className="w-7 h-7 rounded-lg flex items-center justify-center hover:bg-gold/10 transition-colors text-muted hover:text-ink"
              >
                <X size={14} />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
