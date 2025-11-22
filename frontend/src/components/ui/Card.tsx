import React from 'react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode
    className?: string
    hover?: boolean
}

export function Card({ children, className, hover = false, ...props }: CardProps) {
    return (
        <div
            className={cn(
                "bg-surface/30 backdrop-blur-md border border-white/10 rounded-xl p-6 shadow-lg",
                hover && "transition-all duration-300 hover:scale-[1.02] hover:border-primary/50 hover:shadow-primary/10 cursor-pointer",
                className
            )}
            {...props}
        >
            {children}
        </div>
    )
}

export function CardHeader({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("flex flex-col space-y-1.5 mb-4", className)} {...props}>
            {children}
        </div>
    )
}

export function CardTitle({ children, className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
    return (
        <h3 className={cn("font-semibold leading-none tracking-tight text-lg", className)} {...props}>
            {children}
        </h3>
    )
}

export function CardContent({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("", className)} {...props}>
            {children}
        </div>
    )
}

export function CardFooter({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("flex items-center p-6 pt-0", className)} {...props}>
            {children}
        </div>
    )
}
