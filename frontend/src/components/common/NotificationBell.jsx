import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { BellIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { notificationsAPI } from '../../api/client';

export default function NotificationBell() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [open, setOpen] = useState(false);
  const [count, setCount] = useState(0);

  const loadNotifications = useCallback(async () => {
    try {
      const response = await notificationsAPI.get();
      setNotifications(response.data.notifications || []);
      setCount(Number(response.data.count || 0));
    } catch (error) {
      // Authentication or network errors are handled by the page; keep the bell usable.
      setNotifications([]);
      setCount(0);
    }
  }, []);

  useEffect(() => {
    loadNotifications();
    const interval = window.setInterval(loadNotifications, 60000);
    return () => window.clearInterval(interval);
  }, [loadNotifications]);

  const dismiss = async (id) => {
    try {
      await notificationsAPI.dismiss(id);
      setNotifications(current => current.filter(item => item.id !== id));
      setCount(current => Math.max(0, current - 1));
    } catch (error) {
      // Keep it visible if saving the dismissal failed.
    }
  };

  const openNotification = async (notification) => {
    await dismiss(notification.id);
    setOpen(false);
    const destination = notification.action_url || '/dashboard';
    navigate(destination);
    const hash = destination.includes('#') ? destination.split('#')[1] : '';
    if (hash) window.requestAnimationFrame(() => document.getElementById(hash)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => { setOpen(value => !value); if (!open) loadNotifications(); }}
        className="relative p-2 rounded-lg hover:bg-white/5 transition"
        aria-label={`Notifications${count ? `, ${count} pending` : ''}`}
        aria-expanded={open}
      >
        <BellIcon className="w-5 h-5 text-gray-400" />
        {count > 0 && <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full min-w-5 h-5 px-1 flex items-center justify-center">{count > 99 ? '99+' : count}</span>}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] glass-card p-4 z-50 shadow-xl">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-display font-bold">Notifications</h3>
            <button type="button" onClick={() => setOpen(false)} className="text-gray-400 hover:text-white text-sm" aria-label="Close notifications">×</button>
          </div>
          {notifications.length === 0 ? (
            <p className="text-sm text-gray-400">No notifications. You're all caught up!</p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {notifications.map(notification => (
                <div key={notification.id} className="p-3 rounded-lg bg-white/5 hover:bg-white/10 transition">
                  <div className="flex items-start gap-2">
                    <span className="text-xl" aria-hidden="true">{notification.icon || '🔔'}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{notification.title}</p>
                      <p className="text-xs text-gray-400 mt-1">{notification.body}</p>
                      <button type="button" onClick={() => openNotification(notification)} className="text-xs text-[#d2a277] mt-2 inline-block hover:underline">View →</button>
                    </div>
                    <button type="button" onClick={() => dismiss(notification.id)} className="text-gray-500 hover:text-white" aria-label="Dismiss notification"><XMarkIcon className="w-4 h-4" /></button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
