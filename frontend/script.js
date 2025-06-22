document.addEventListener('DOMContentLoaded', () => {
    const empleadoForm = document.getElementById('empleado-form');
    const btnCancel = document.getElementById('btn-cancel');
    const btnMasivo = document.getElementById('btn-masivo');
    const empleadosTable = document.querySelector('#empleados-table tbody');
    const formTitle = document.getElementById('form-title');
    
    let isEditing = false;
    let currentEditId = null;

    // Cargar empleados al inicio
    fetchEmpleados();

    // Event Listeners
    empleadoForm.addEventListener('submit', handleSubmit);
    btnCancel.addEventListener('click', cancelEdit);
    btnMasivo.addEventListener('click', handleMasivo);

    // Obtener empleados
    async function fetchEmpleados() {
        try {
            const response = await fetch('http://localhost:8000/empleados');
            const empleados = await response.json();
            renderEmpleados(empleados);
        } catch (error) {
            console.error('Error:', error);
            alert('Error al obtener empleados');
        }
    }

    // Renderizar tabla
    function renderEmpleados(empleados) {
        empleadosTable.innerHTML = '';
        empleados.forEach(empleado => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${empleado.id}</td>
                <td>${empleado.nombre}</td>
                <td>${empleado.puesto}</td>
                <td>${empleado.salario.toFixed(2)}</td>
                <td class="actions">
                    <button class="btn-edit" data-id="${empleado.id}">Editar</button>
                    <button class="btn-delete" data-id="${empleado.id}">Eliminar</button>
                </td>
            `;
            empleadosTable.appendChild(row);
        });

        // Agregar event listeners a los botones
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.dataset.id;
                editEmpleado(id);
            });
        });

        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.dataset.id;
                deleteEmpleado(id);
            });
        });
    }

    // Manejar envío del formulario
    async function handleSubmit(e) {
        e.preventDefault();
        
        const empleado = {
            nombre: document.getElementById('nombre').value,
            puesto: document.getElementById('puesto').value,
            salario: parseFloat(document.getElementById('salario').value)
        };

        try {
            let response;
            if (isEditing) {
                response = await fetch(`http://localhost:8000/empleados/${currentEditId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(empleado)
                });
            } else {
                response = await fetch('http://localhost:8000/empleados', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(empleado)
                });
            }

            if (response.ok) {
                resetForm();
                fetchEmpleados();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Error en la operación');
            }
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }

    // Editar empleado
    async function editEmpleado(id) {
        try {
            const response = await fetch(`http://localhost:8000/empleados/${id}`);
            if (!response.ok) throw new Error('Empleado no encontrado');
            
            const empleado = await response.json();
            
            document.getElementById('empleado-id').value = id;
            document.getElementById('nombre').value = empleado.nombre;
            document.getElementById('puesto').value = empleado.puesto;
            document.getElementById('salario').value = empleado.salario;
            
            isEditing = true;
            currentEditId = id;
            formTitle.textContent = 'Editar Empleado';
            btnCancel.style.display = 'inline-block';
            
            // Scroll al formulario
            document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }

    // Cancelar edición
    function cancelEdit() {
        resetForm();
    }

    // Resetear formulario
    function resetForm() {
        empleadoForm.reset();
        document.getElementById('empleado-id').value = '';
        isEditing = false;
        currentEditId = null;
        formTitle.textContent = 'Agregar Nuevo Empleado';
        btnCancel.style.display = 'none';
    }

    // Eliminar empleado
    async function deleteEmpleado(id) {
        if (!confirm('¿Estás seguro de eliminar este empleado?')) return;
        
        try {
            const response = await fetch(`http://localhost:8000/empleados/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                fetchEmpleados();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Error al eliminar');
            }
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }

    // Inserción masiva
    async function handleMasivo() {
        const data = document.getElementById('empleados-masivos').value;
        if (!data) {
            alert('Por favor ingrese datos para inserción masiva');
            return;
        }
        
        try {
            const empleados = JSON.parse(data);
            if (!Array.isArray(empleados)) {
                throw new Error('Formato inválido. Debe ser un array de empleados');
            }
            
            const response = await fetch('http://localhost:8000/empleados/masivo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ empleados })
            });
            
            if (response.ok) {
                alert('Empleados insertados correctamente');
                document.getElementById('empleados-masivos').value = '';
                fetchEmpleados();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Error en inserción masiva');
            }
        } catch (error) {
            console.error('Error:', error);
            alert(`Error: ${error.message}`);
        }
    }
});