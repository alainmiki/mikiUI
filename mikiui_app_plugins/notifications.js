/** MikiUI Notifications Plugin - Alpine.js Component */

document.addEventListener('alpine:init', () => {
    Alpine.data('mikiNotifications', (initial = []) => ({
        notifications: [...initial],
        maxVisible: 5,
        get visibleNotifications() {
            return this.notifications
                .filter(n => !n.read)
                .slice(-this.maxVisible);
        },
        dismiss(id) {
            const idx = this.notifications.findIndex(n => n.id === id);
            if (idx !== -1) {
                this.notifications.splice(idx, 1);
            }
        },
        dismissAll() {
            this.notifications.forEach(n => n.read = true);
        },
        init() {
            this.$watch('notifications', () => {
                this.notifications = this.notifications.slice(-20);
            });
            if (typeof WebSocket !== 'undefined') {
                this.connectWebSocket();
            }
        },
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${window.location.host}/ws/notifications`);
            ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.type === 'notifications') {
                        msg.data.forEach(n => {
                            if (!this.notifications.find(existing => existing.id === n.id)) {
                                this.notifications.push(n);
                            }
                        });
                    }
                } catch (e) {
                    console.error('Notification WS error:', e);
                }
            };
        },
        iconForType(type) {
            const icons = {
                info: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
                success: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
                warning: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>`,
                error: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
            };
            return icons[type] || icons.info;
        },
        typeClasses(type) {
            const classes = {
                info: 'border-blue-400 bg-blue-50 text-blue-800',
                success: 'border-green-400 bg-green-50 text-green-800',
                warning: 'border-yellow-400 bg-yellow-50 text-yellow-800',
                error: 'border-red-400 bg-red-50 text-red-800',
            };
            return classes[type] || classes.info;
        },
        iconClasses(type) {
            const classes = {
                info: 'text-blue-500',
                success: 'text-green-500',
                warning: 'text-yellow-500',
                error: 'text-red-500',
            };
            return classes[type] || classes.info;
        }
    }));
});
