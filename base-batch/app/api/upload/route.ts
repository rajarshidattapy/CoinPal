import { NextRequest, NextResponse } from "next/server";
import { pinata } from "@/utils/config";

export const config = {
    api: {
        bodyParser: false,
    }
};

export async function POST(request: NextRequest) {
    try {
        const data = await request.formData();
        const file: File | null = data.get("file") as unknown as File;
        if (!file) {
            return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
        }
        const { cid } = await pinata.upload.public.file(file);
        const url = `${pinata.gateways.config?.pinataGateway}/ipfs/${cid}?expires=3600`;
        // console.log(pinata.gateways.config?.pinataGateway);
        return NextResponse.json({ url: url }, { status: 200 });
    } catch (e) {
        console.log(e);
        return NextResponse.json(
            { error: "Internal Server Error" },
            { status: 500 }
        );
    }
}
