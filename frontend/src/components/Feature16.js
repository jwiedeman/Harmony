import { Timer, Zap, ZoomIn } from "lucide-react";

const Feature16 = () => {
  return (
    <section className="py-32">
      <div className="container">
        <h2 className="text-3xl font-medium lg:text-4xl">
          Get real-time alerts and dashboard snapshots—fix staffing, menu, and flow issues before they cost you.
        </h2>
        <div className="mt-14 grid gap-6 lg:mt-20 lg:grid-cols-3">
          <div className="rounded-lg bg-accent p-5">
            <span className="mb-8 flex size-12 items-center justify-center rounded-full bg-background">
              <Timer className="size-6" />
            </span>
            <h3 className="mb-2 text-xl font-medium">Still running your nights blind?</h3>
            <p className="leading-7 text-muted-foreground">
              Stay ahead with instant insights into floor performance.
            </p>
          </div>
          <div className="rounded-lg bg-accent p-5">
            <span className="mb-8 flex size-12 items-center justify-center rounded-full bg-background">
              <ZoomIn className="size-6" />
            </span>
            <h3 className="mb-2 text-xl font-medium">Empty tables after rush?</h3>
            <p className="leading-7 text-muted-foreground">
              Spot traffic dips and act fast to fill your seats.
            </p>
          </div>
          <div className="rounded-lg bg-accent p-5">
            <span className="mb-8 flex size-12 items-center justify-center rounded-full bg-background">
              <Zap className="size-6" />
            </span>
            <h3 className="mb-2 text-xl font-medium">Unbalanced staff scheduling?</h3>
            <p className="leading-7 text-muted-foreground">
              Optimize staffing to match demand and avoid burnout.
            </p>
          </div>
        </div>
        <ul className="mt-8 list-disc pl-5 text-muted-foreground">
          <li>Dish waste or unpopular menu items?</li>
          <li>Poor reviews from slow service?</li>
        </ul>
      </div>
    </section>
  );
};

export { Feature16 };
