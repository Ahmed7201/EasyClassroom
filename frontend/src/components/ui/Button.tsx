import React from 'react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline'
    size?: 'sm' | 'md' | 'lg' | 'icon'
    isLoading?: boolean
}

export function Button({
    className,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    children,
    disabled,
    ...props
}: ButtonProps) {
    const variants = {
        primary: "bg-primary text-background hover:bg-primary/90 shadow-lg shadow-primary/20",
        secondary: "bg-secondary text-white hover:bg-secondary/90",
        danger: "bg-danger text-white hover:bg-danger/90",
        ghost: "hover:bg-white/10 text-text",
        outline: "border border-white/20 hover:bg-white/5 text-text"
    }

    const sizes = {
        sm: "h-8 px-3 text-xs",
        md: "h-10 px-4 py-2",
        lg: "h-12 px-8 text-lg",
        icon: "h-10 w-10 p-2 flex items-center justify-center"
    }

    return (
        <button
            className={cn(
                "inline-flex items-center justify-center rounded-lg font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50 active:scale-95",
                variants[variant],
                sizes[size],
                className
            )}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading ? (
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            ) : null}
            {children}
        </button>
    )
}
