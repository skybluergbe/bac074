#!/usr/bin/env python3
import asyncio
from bacpypes3.local.device import DeviceObject
from bacpypes3.pdu import Address, IPv4Address
from bacpypes3.primitivedata import ObjectIdentifier, Real
from bacpypes3.apdu import ReadPropertyRequest, WritePropertyRequest
from bacpypes3.ipv4.app import NormalApplication
from bacpypes3.constructeddata import Any
from bacpypes3.tag import Tag, TagList

async def read_property(app, target_device, object_id, property_id):
    request = ReadPropertyRequest(
        objectIdentifier=ObjectIdentifier(object_id),
        propertyIdentifier=property_id
    )
    request.pduDestination = Address(target_device)
    response = await app.request(request)
    if response:
        return response.propertyValue.cast_out(Real)
    return None

async def write_priority_null(app, target_device, object_id, property_id, priority):
    # Null 태그 직접 생성 (Context Tag 5, 값 없음)
    null_tag = Tag()
    null_tag.tagNumber = 5
    null_tag.tagClass = 1  # Context Tag
    null_tag.tagValue = 0  # Null은 값이 없음

    tag_list = TagList()
    tag_list.append(null_tag)

    bacnet_value = Any()
    bacnet_value.tagList = tag_list

    request = WritePropertyRequest(
        objectIdentifier=ObjectIdentifier(object_id),
        propertyIdentifier=property_id,
        propertyValue=bacnet_value,
        priority=priority
    )
    request.pduDestination = Address(target_device)
    response = await app.request(request)
    if response:
        print(f"우선순위 {priority}에 Null 값 쓰기 성공")
    else:
        print("쓰기 실패 또는 응답 없음")

async def main():
    device = DeviceObject(
        objectName="LocalDevice",
        objectIdentifier=("device", 1234),
        maxApduLengthAccepted=1024,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=999
    )
    local_address = IPv4Address("200.0.0.234/24")
    app = NormalApplication(device, local_address)

    target_ip = "200.0.0.162"
    obj_id = ("analogOutput", 1)
    prop_id = "presentValue"
    priority_slot = 2

    print("쓰기 전 값 읽기:")
    val_before = await read_property(app, target_ip, obj_id, prop_id)
    print(f"현재 값: {val_before}")

    print("Null 값 우선순위 쓰기 시도 중...")
    await write_priority_null(app, target_ip, obj_id, prop_id, priority_slot)

    await asyncio.sleep(1)

    print("쓰기 후 값 읽기:")
    val_after = await read_property(app, target_ip, obj_id, prop_id)
    print(f"현재 값: {val_after}")

if __name__ == "__main__":
    asyncio.run(main())
