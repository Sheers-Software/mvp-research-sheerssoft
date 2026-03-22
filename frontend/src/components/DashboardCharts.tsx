'use client';

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

interface VolumeChartProps {
    data: {
        labels: string[];
        inquiries: number[];
        leads: number[];
    };
}

export function VolumeChart({ data }: VolumeChartProps) {
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'top' as const },
        },
        scales: {
            y: { beginAtZero: true },
        },
    };

    const chartData = {
        labels: data.labels,
        datasets: [
            {
                label: 'Total Inquiries',
                data: data.inquiries,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.3,
                fill: true,
            },
            {
                label: 'Leads Captured',
                data: data.leads,
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.3,
                fill: true,
            },
        ],
    };

    return <Line options={options} data={chartData} />;
}

interface BreakdownProps {
    data: Record<string, number>;
}

export function ChannelChart({ data }: BreakdownProps) {
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'right' as const },
        },
    };

    const labels = Object.keys(data).map(k => k.charAt(0).toUpperCase() + k.slice(1));
    const values = Object.values(data);

    const chartData = {
        labels,
        datasets: [
            {
                data: values,
                backgroundColor: [
                    'rgba(37, 211, 102, 0.8)', // WhatsApp Green
                    'rgba(59, 130, 246, 0.8)', // Web Blue
                    'rgba(245, 158, 11, 0.8)', // Email Orange
                    'rgba(156, 163, 175, 0.8)'
                ],
                borderWidth: 0,
            },
        ],
    };

    return <Doughnut options={options} data={chartData} />;
}
