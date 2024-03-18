import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const get_login = query({
    args: {
        username: v.string()},

    handler: async ({ db }, args) => {
        
        return await db.query("users").filter((q) => q.eq(q.field("username"), args.username)).collect();
    },
});

export const complete_signup = mutation({
    args: {
        username: v.string(),
        password: v.string(),
        level: v.string()},

    handler: async ({ db }, args) => {
        
        return await db.insert("users", args)
    },
});

export const get_categories = query({
    args: {
        uid: v.string()},

    handler: async ({ db }, args) => {
        
        return await db.query("categories").filter((q) => q.eq(q.field("uid"), args.uid)).collect();
    },
});

export const create_categories = mutation({
    args: {
        uid: v.string(),
        categories: v.array(v.string()),
        category_det: v.array(v.string()),
        categories_dict: v.any(),
        history_dict : v.any(),
    },

    handler: async ({ db }, args) => {

        let prev = await db.query("categories").filter((q) => q.eq(q.field("uid"), args.uid)).collect();

        if (prev.length != 0) {
            return await db.patch(prev[0]["_id"], args)
        }
        else{
            return await db.insert("categories", args)
        }
        
    },
});