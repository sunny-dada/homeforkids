/** Button - HDS CVA 패턴 */
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import React from "react";

const buttonVariants = cva(
  "relative w-full h-12 flex items-center justify-center gap-1 rounded-md text-base font-normal transition-colors disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        primary:
          "bg-primary text-primary-foreground active:bg-primary-900 disabled:bg-background-second disabled:text-foreground-muted",
        secondary:
          "bg-white text-primary border border-solid border-primary active:text-primary-700 disabled:text-foreground-muted disabled:border-foreground-muted",
        tertiary:
          "bg-background-second text-primary active:text-primary-700 disabled:text-foreground-muted",
        outline:
          "bg-white text-foreground border border-solid border-border hover:border-primary hover:bg-background-second disabled:opacity-50",
      },
    },
    defaultVariants: { variant: "primary" },
  },
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant }), className)}
      {...props}
    />
  ),
);
Button.displayName = "Button";
