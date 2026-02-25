from app.core.unit_of_work import UnitOfWork
from app.orders.models.orders_model import Order
from app.orders.repository import OrderRepository
from app.inventory.repositories.product_repo import ProductRepository
from app.orders.schemas.command import CreateOrderCommand, OrderDTO, OrderItemDTO


class OrderService:

    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        uow: UnitOfWork,
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.uow = uow

    async def create_order(
            self,
            command: CreateOrderCommand
    ) -> OrderDTO:

        async with self.uow as session:

            product_repo = ProductRepository(session)
            order_repo = OrderRepository(session)

            order = Order.create()
            total_amount = 0

            for item_cmd in command.items:

                product = await product_repo.get_by_id(
                    item_cmd.product_id
                )

                if not product:
                    raise ValueError("Product not found")

                unit_price = product.price
                subtotal = unit_price * item_cmd.quantity
                total_amount += subtotal

                order.add_item(
                    product_id=item_cmd.product_id,
                    quantity=item_cmd.quantity,
                    unit_price=unit_price,
                )

            order.set_total_amount(total_amount)

            await order_repo.create(order)

            await session.flush()

            return OrderDTO(
                id=order.id,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at,
                items=[
                    OrderItemDTO(
                        product_id=i.product_id,
                        quantity=i.quantity,
                        unit_price=i.unit_price,
                    )
                    for i in order.items
                ],
            )