#!/bin/bash
# Agregar categories: [articulo] a todos los posts excepto index.qmd

for file in posts/*.qmd; do
  # Saltar el index.qmd
  if [[ "$file" == "posts/index.qmd" ]]; then
    continue
  fi
  
  # Verificar si ya tiene categories
  if grep -q "^categories:" "$file"; then
    echo "⏭️  $file ya tiene categories, saltando"
  else
    # Insertar categories después de la línea de date
    sed -i '' '/^date:/a\
categories: [articulo]
' "$file"
    echo "✅ Agregado categories a $file"
  fi
done