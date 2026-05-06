/** Badge - HDS CVA 패턴 */
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2.5 py-1 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary-100 text-primary",
        safe: "bg-safety-safe-bg text-safety-safe",
        normal: "bg-safety-normal-bg text-safety-normal",
        caution: "bg-safety-caution-bg text-safety-caution",
        secondary: "bg-background-second text-foreground-second",
      },
      size: {
        sm: "text-xs px-2 py-0.5",
        md: "text-sm px-2.5 py-1",
        lg: "text-base px-3 py-1.5 font-bold",
      },
    },
    defaultVariants: { variant: "default", size: "md" },
  },
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant, size }), className)} {...props} />
  );
}
