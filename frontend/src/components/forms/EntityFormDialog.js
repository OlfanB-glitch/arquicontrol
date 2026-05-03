import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export function EntityFormDialog({
  open,
  onOpenChange,
  title,
  description,
  fields,
  initialValues,
  onSubmit,
  isSubmitting,
}) {
  const { handleSubmit, register, reset, formState: { errors } } = useForm();

  useEffect(() => {
    const defaults = fields.reduce((accumulator, field) => {
      accumulator[field.name] = initialValues?.[field.name] ?? (field.type === "select" ? field.options?.[0] || "" : "");
      return accumulator;
    }, {});
    reset(defaults);
  }, [fields, initialValues, open, reset]);

  async function submitForm(values) {
    const payload = fields.reduce((accumulator, field) => {
      const currentValue = values[field.name];
      accumulator[field.name] = field.type === "number" ? Number(currentValue || 0) : currentValue;
      return accumulator;
    }, {});
    await onSubmit(payload);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl rounded-sm border-zinc-200 bg-white shadow-2xl">
        <DialogHeader>
          <DialogTitle data-testid="entity-form-dialog-title">{title}</DialogTitle>
          <DialogDescription data-testid="entity-form-dialog-description">{description}</DialogDescription>
        </DialogHeader>

        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit(submitForm)}>
          {fields.map((field) => (
            <label key={field.name} className={field.type === "textarea" ? "md:col-span-2" : "block"}>
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.12em] text-zinc-500">
                {field.label}
              </span>

              {field.type === "textarea" ? (
                <Textarea
                  {...register(field.name, { required: field.required ? `${field.label} es obligatorio` : false })}
                  className="min-h-[120px] rounded-sm border-zinc-300 shadow-none focus-visible:ring-zinc-900"
                  data-testid={`entity-form-field-${field.name}`}
                />
              ) : field.type === "select" ? (
                <select
                  {...register(field.name, { required: field.required ? `${field.label} es obligatorio` : false })}
                  className="flex h-10 w-full rounded-sm border border-zinc-300 bg-white px-3 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-900"
                  data-testid={`entity-form-field-${field.name}`}
                >
                  {field.options?.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              ) : (
                <Input
                  type={field.type}
                  min={field.min}
                  step={field.type === "number" ? "any" : undefined}
                  {...register(field.name, { required: field.required ? `${field.label} es obligatorio` : false })}
                  className="rounded-sm border-zinc-300 shadow-none focus-visible:ring-zinc-900"
                  data-testid={`entity-form-field-${field.name}`}
                />
              )}

              {errors[field.name] ? (
                <span className="mt-2 block text-sm text-red-600" data-testid={`entity-form-error-${field.name}`}>
                  {errors[field.name]?.message}
                </span>
              ) : null}
            </label>
          ))}

          <DialogFooter className="md:col-span-2">
            <Button type="button" variant="outline" className="rounded-sm border-zinc-300" onClick={() => onOpenChange(false)} data-testid="entity-form-cancel-button">
              Cancelar
            </Button>
            <Button type="submit" className="rounded-sm bg-zinc-900 text-white hover:bg-zinc-800" disabled={isSubmitting} data-testid="entity-form-submit-button">
              {isSubmitting ? "Guardando..." : "Guardar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}